import xml.etree.ElementTree as ET
import sys
import re
import sqlite3
from pdb import set_trace

conn = sqlite3.connect('vms.db')
cur = conn.cursor()


def elt_metadata(elem, type=''):
    return {
        'code': select(elem, 'PublicId'),
        'version': select(elem, 'Version'),
        'term': select(elem, 'LongName'),
        'type': type,
        'shortName': select(elem, 'PreferredName'),
        'definition': select(elem, 'PreferredDefinition'),
        'context': select(elem, 'ContextName'),
    }


def do_stmt(data, table):
    stmt = f"""
    INSERT or ignore INTO {table} ({','.join(data.keys())})
    VALUES ({','.join(['?']*len(data))})
    """
    cur.execute(stmt, tuple(data.values()))


select = lambda elt, mbr: elt.find(mbr).text if elt.find(mbr) is not None else ''
cde = None
vdm = None
xml_file = sys.argv[1:]

for xml in xml_file:
    print(xml)
    if not re.match(".*[.]xml$",xml):
        print(f"File '{xml}' not an xml file; skipping")
        continue
    context = ET.iterparse(xml, events=('start', 'end'))
    for event, elem in context:
        if event == 'end':
            if elem.tag == 'DataElement':
                if not select(elem, 'WORKFLOWSTATUS') or select(elem, 'WORKFLOWSTATUS').find('RETIRED') >= 0:
                    continue

                cde = {
                    'code': select(elem,'PUBLICID'),
                    'type': 'CDE',
                    'version': select(elem, 'VERSION'),
                    'term': select(elem, 'LONGNAME'),
                    'definition': select(elem, 'PREFERREDDEFINITION'),
                    'shortName': select(elem, 'PREFERREDNAME'),
                    'context': select(elem, 'CONTEXTNAME'),
                }
                do_stmt(cde,'cde')

                vdm_elt = elem.find('VALUEDOMAIN')
                if vdm_elt is None:
                    continue
                if select(vdm_elt, 'ValueDomainType') != 'Enumerated':
                    continue
                vdm = {
                    'code': select(vdm_elt, 'PublicId'),
                    'type': "VDM",
                    'version': select(vdm_elt, 'Version'),
                    'context': select(vdm_elt, 'ContextName'),
                    'term': select(vdm_elt, 'LongName'),
                    'shortName': select(vdm_elt, 'PreferredName'),
                    'definition': select(vdm_elt, 'PreferredDefinition'),
                }
                do_stmt(vdm,'vdm')
                pvs_elt = vdm_elt.find('PermissibleValues')
                if pvs_elt is not None:
                    for pv in pvs_elt.findall('PermissibleValues_ITEM'):
                        pv_rec = {
                            "code": select(pv,'VMPUBLICID'),
                            "type": "PV",
                            "version": select(pv, 'VMVERSION') or 'none',
                            "term": select(pv, 'VALUEMEANING'),
                            "definition": select(pv, 'MEANINGDESCRIPTION'),
                            "concept_code": select(pv, 'MEANINGCONCEPTS'),
                            "concept_origin": select(pv, 'MEANINGCONCEPTORIGIN'),
                            }
                        if not pv_rec['code']:
                            continue
                        do_stmt(pv_rec, 'pv')

                        link = {"vdm_code": vdm['code'], "vdm_version": vdm['version'],
                                "pv_code": pv_rec['code'], "pv_version": pv_rec['version']}
                        do_stmt(link, 'vdm_pv')
                link = {"cde_code": cde['code'], "cde_version": cde["version"],
                        "vdm_code": vdm['code'], "vdm_version": vdm["version"]}
                do_stmt(link, 'cde_vdm')

                dec_elem = elem.find('DATAELEMENTCONCEPT')
                dec = elt_metadata(dec_elem, 'DEC')
                do_stmt(dec,'dec')
                link = {
                    'cde_code': cde['code'],
                    'cde_version': cde['version'],
                    'dec_code': dec['code'],
                    'dec_version': dec['version']
                    }
                do_stmt(link, 'cde_dec')
                oc_elem = dec_elem.find('ObjectClass')
                oc = elt_metadata(oc_elem, 'OC')
                do_stmt(oc, 'oc')
                concepts = oc_elem.find('ConceptDetails').findall('ConceptDetails_ITEM')
                for cpt in concepts:
                    rec = {
                        'oc_code': oc['code'],
                        'oc_version': oc['version'],
                        'concept_code': select(cpt, 'PREFERRED_NAME'),
                    }
                    do_stmt(rec, 'oc_ncit')
                    pass
                pr_elem = dec_elem.find('Property')
                pr = elt_metadata(pr_elem, 'PR')
                do_stmt(pr, 'pr')
                concepts = pr_elem.find('ConceptDetails').findall('ConceptDetails_ITEM')
                for cpt in concepts:
                    rec = {
                        'pr_code': pr['code'],
                        'pr_version': pr['version'],
                        'concept_code': select(cpt, 'PREFERRED_NAME'),
                    }
                    do_stmt(rec, 'pr_ncit')
                    pass
                link = {
                    'dec_code': dec['code'],
                    'dec_version': dec['version'],
                    'oc_code': oc['code'],
                    'oc_version': oc['version'],
                    }
                do_stmt(link, 'dec_oc')
                link = {
                    'dec_code': dec['code'],
                    'dec_version': dec['version'],
                    'pr_code': pr['code'],
                    'pr_version': pr['version'],
                    }
                do_stmt(link, 'dec_pr')

                conn.commit()

# create pv -> ncit concept table
cur.execute("select count(*) from pv_ncit")
num = cur.fetchone()
num = num[0]
if num == 0:
    cur.execute("select * from pv where concept_origin LIKE '%NCI%'")
    pvs = cur.fetchall()

    for pv in pvs:
        cc = pv['concept_code'].split(', ')
        for c in cc:
            link = {
                'pv_code': pv['code'],
                'pv_version': pv['version'],
                'concept_code': c,
            }
            do_stmt(link, 'pv_ncit')
            pass

        conn.commit()

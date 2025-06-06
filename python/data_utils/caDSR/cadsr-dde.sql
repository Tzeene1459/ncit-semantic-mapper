CREATE TABLE IF NOT EXISTS pv  (
  code text not null,
  version text not null,
  type text,
  term text,
  definition text,
  concept_code text,
  concept_origin, md5 text,
  unique (code, version, type, term, definition, concept_code, concept_origin)
  );
CREATE TABLE IF NOT EXISTS vdm  (
  code text not null,
  version text not null,
  type text,
  definition text,
  context text,
  term text,
  shortName text, md5 text,
  unique (code, version, type, context, definition, term, shortName )
  );
CREATE TABLE IF NOT EXISTS cde (
  code text not null,
  type text,
  version text not null,
  definition text,
  shortName text,
  context text,
  term text, md5 text,
  unique (code, version, type, context, definition, term, shortName )
  );
CREATE TABLE IF NOT EXISTS dec (
  code text not null,
  type text,
  version text not null,
  term text,
  definition text,
  shortName text,
  context text, md5 text,
  unique (code, version, type, context, definition, term, shortName )
  );
CREATE TABLE IF NOT EXISTS oc (
  code text not null,
  type text,
  version text not null,
  term text,
  definition text,
  shortName text,
  context text,
  unique (code, version, type, context, definition, term, shortName )
  );
CREATE TABLE IF NOT EXISTS pr (
  code text not null,
  type text,
  version text not null,
  definition text,
  term text,
  shortName text,
  context text,
  unique (code, version, type, definition, context, term, shortName )
  );
CREATE TABLE IF NOT EXISTS cde_vdm (
  cde_code text not null,
  cde_version text not null,
  vdm_code text not null,
  vdm_version text not null,
  unique (cde_code, cde_version, vdm_code, vdm_version)
  );
CREATE TABLE IF NOT EXISTS cde_dec (
  cde_code text not null,
  cde_version text not null,
  dec_code text not null,
  dec_version text not null,
  unique (cde_code, cde_version, dec_code, dec_version)
  );
CREATE TABLE IF NOT EXISTS vdm_pv (
  vdm_code text not null,
  vdm_version text not null,
  pv_code text not null,
  pv_version text not null,
  unique ( vdm_code, vdm_version, pv_code, pv_version)
  );
CREATE TABLE IF NOT EXISTS oc_ncit (
  oc_code text not null,
  oc_version text not null,
  concept_code text not null,
  unique (oc_code, oc_version, concept_code)
  );
CREATE TABLE IF NOT EXISTS pr_ncit (
  pr_code text not null,
  pr_version text not null,
  concept_code text not null,
  unique (pr_code, pr_version, concept_code)
  );
CREATE TABLE IF NOT EXISTS dec_pr (
  dec_code text not null,
  dec_version text not null,
  pr_code text not null,
  pr_version text not null,
  unique (dec_code, dec_version,pr_code, pr_version)
  );
CREATE TABLE IF NOT EXISTS dec_oc (
  dec_code text not null,
  dec_version text not null,
  oc_code text not null,
  oc_version text not null,
  unique (dec_code, dec_version,oc_code, oc_version)
  );
CREATE TABLE IF NOT EXISTS pv_ncit (pv_code text, pv_version text, concept_code text);

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE SCHEMA public;
ALTER SCHEMA public OWNER TO postgres;
COMMENT ON SCHEMA public IS 'standard public schema';

SET default_tablespace = '';
SET default_with_oids = false;

CREATE TABLE public.timeseries (
    max integer,
    unixtstamp integer
);
ALTER TABLE public.timeseries OWNER TO yggindex;

CREATE TABLE public.yggindex (
    ipv6 character varying(46),
    coords character varying,
    unixtstamp character varying(30),
    name character varying
);
ALTER TABLE public.yggindex OWNER TO yggindex;

CREATE TABLE public.yggnodeinfo (
    ipv6 character varying(46),
    nodeinfo character varying,
    "timestamp" character varying(12)
);
ALTER TABLE public.yggnodeinfo OWNER TO yggindex;

ALTER TABLE ONLY public.yggindex
    ADD CONSTRAINT yggindex_ipv6_key UNIQUE (ipv6);

ALTER TABLE ONLY public.yggnodeinfo
    ADD CONSTRAINT yggnodeinfo_ipv6_key UNIQUE (ipv6);

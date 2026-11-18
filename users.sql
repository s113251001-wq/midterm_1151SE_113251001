-- Adminer 6.1.0 PostgreSQL 17.6 dump

DROP TABLE IF EXISTS "public"."users";

CREATE TABLE "public"."users" (
    "id" serial NOT NULL,
    "username" character varying(50) NOT NULL,
    "password_hash" character varying(255) NOT NULL,
    "role" character varying(20) NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_role_check" CHECK (((role)::text = ANY ((ARRAY['author'::character varying, 'editor'::character varying])::text[])))
);

CREATE UNIQUE INDEX users_username_key ON "public"."users" USING btree (username);



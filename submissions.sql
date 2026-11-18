-- Adminer 6.1.0 PostgreSQL 17.6 dump

DROP TABLE IF EXISTS "public"."submissions";

CREATE TABLE "public"."submissions" (
    "id" serial NOT NULL,
    "author_id" integer NOT NULL,
    "category" character varying(50) NOT NULL,
    "title" character varying(200) NOT NULL,
    "content" text NOT NULL,
    "status" character varying(10) DEFAULT '編輯中' NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "submissions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "submissions_status_check" CHECK (((status)::text = ANY ((ARRAY['編輯中'::character varying, '審查中'::character varying, '已通過'::character varying])::text[])))
);

CREATE INDEX idx_submissions_author_id ON "public"."submissions" USING btree (author_id);

CREATE INDEX idx_submissions_status ON "public"."submissions" USING btree (status);


ALTER TABLE ONLY "public"."submissions" ADD CONSTRAINT "submissions_author_id_fkey" FOREIGN KEY (author_id) REFERENCES "public"."users"(id) ON DELETE CASCADE;

-- 2026-11-18 17:11:12 UTC

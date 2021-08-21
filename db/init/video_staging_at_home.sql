-- Table: public.video_staging_at_home

-- DROP TABLE public.video_staging_at_home;

CREATE TABLE public.video_staging_at_home
(
    video_id character varying(15) COLLATE pg_catalog."default" NOT NULL,
    published_at character varying(50) COLLATE pg_catalog."default",
    title character varying(100) COLLATE pg_catalog."default",
    description character varying COLLATE pg_catalog."default",
    category_id character varying(5) COLLATE pg_catalog."default",
    duration character varying(10) COLLATE pg_catalog."default",
    definition character varying(5) COLLATE pg_catalog."default",
    view_count integer,
    like_count integer,
    dislike_count integer,
    favorite_count integer,
    comment_count integer,
    embed_html character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.video_staging_at_home
    OWNER to postgres;
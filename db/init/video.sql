-- Table: public.video

-- DROP TABLE public.video;

CREATE TABLE public.video
(
    video_id character varying(15) COLLATE pg_catalog."default" NOT NULL,
    published_at timestamp with time zone,
    title character varying(100) COLLATE pg_catalog."default",
    description character varying COLLATE pg_catalog."default",
    category_id character varying(5) COLLATE pg_catalog."default",
    duration integer,
    definition character varying(5) COLLATE pg_catalog."default",
    view_count integer,
    like_count integer,
    dislike_count integer,
    favorite_count integer,
    comment_count integer,
    embed_html character varying COLLATE pg_catalog."default",
    last_modified timestamp with time zone,
    CONSTRAINT video_pkey PRIMARY KEY (video_id)
)

TABLESPACE pg_default;

ALTER TABLE public.video
    OWNER to postgres;
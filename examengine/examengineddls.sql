-- public.users definition

-- Drop table

-- DROP TABLE public.users;

CREATE TABLE public.users (
	id serial4 NOT NULL,
	username varchar NULL,
	hashed_password varchar NOT NULL,
	"role" varchar NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE INDEX ix_users_id ON public.users USING btree (id);
CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);

-- public."options" definition

-- Drop table

-- DROP TABLE public."options";

CREATE TABLE public."options" (
	id int4 NOT NULL,
	"text" text NOT NULL,
	is_correct bool DEFAULT false NULL,
	question_id int4 NULL,
	CONSTRAINT options_pkey PRIMARY KEY (id)
);


-- public."options" foreign keys

ALTER TABLE public."options" ADD CONSTRAINT options_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;

-- public.questions definition

-- Drop table

-- DROP TABLE public.questions;

CREATE TABLE public.questions (
	id int4 NOT NULL,
	"text" text NOT NULL,
	test_id int4 NULL,
	CONSTRAINT questions_pkey PRIMARY KEY (id)
);


-- public.questions foreign keys

ALTER TABLE public.questions ADD CONSTRAINT questions_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.tests(id) ON DELETE CASCADE;

-- public.results definition

-- Drop table

-- DROP TABLE public.results;

CREATE TABLE public.results (
	id int4 NOT NULL,
	user_id int4 NULL,
	score int4 NULL,
	test_id int4 NULL,
	CONSTRAINT results_pkey PRIMARY KEY (id)
);


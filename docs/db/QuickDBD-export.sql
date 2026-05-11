-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "user" (
    "id" int   NOT NULL,
    "organization_id" int   NULL,
    "first_name" varchar(50)   NOT NULL,
    "last_name" varchar(50)   NOT NULL,
    "login" varchar(50)   NOT NULL,
    "mail" varchar(50)   NOT NULL,
    -- (hash)
    "password" varchar(255)   NOT NULL,
    CONSTRAINT "pk_user" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_user_mail" UNIQUE (
        "mail"
    )
);

CREATE TABLE "organization" (
    "id" int   NOT NULL,
    "org_owner_id" int   NOT NULL,
    "name" varchar(50)   NOT NULL,
    "description" text   NULL,
    CONSTRAINT "pk_organization" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "project" (
    "id" int   NOT NULL,
    "project_owner_id" int   NOT NULL,
    "organization_id" int   NULL,
    "name" varchar(50)   NOT NULL,
    CONSTRAINT "pk_project" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "user_project" (
    "user_id" int   NOT NULL,
    "project_id" int   NOT NULL,
    "role_id" int   NOT NULL
);

CREATE TABLE "role" (
    "id" int   NOT NULL,
    "name" varchar(50)   NOT NULL,
    "project_id" int   NOT NULL,
    "can_write_tickets" bool   NOT NULL,
    "can_help" bool   NOT NULL,
    "can_assign_help" bool   NOT NULL,
    "can_make_roles" bool   NOT NULL,
    "can_change_roles" bool   NOT NULL,
    "can_assign_people_to_project" bool   NOT NULL,
    CONSTRAINT "pk_role" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "problem" (
    "id" int   NOT NULL,
    "user_id" int   NOT NULL,
    "project_id" int   NOT NULL,
    "helper_id" int   NULL,
    "title" varchar(50)   NOT NULL,
    "status" varchar(50)   NOT NULL,
    "categories" text   NOT NULL,
    "priority_level" int   NOT NULL,
    "description" text   NOT NULL,
    "creation_date" datetime   NOT NULL,
    "closing_date" datetime   NULL,
    CONSTRAINT "pk_problem" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "problem_logs" (
    "id" int   NOT NULL,
    "problem_id" int   NOT NULL,
    "person_id" int   NOT NULL,
    -- (priority_level change albo comment albo deleted_helper albo added helper albo change projects)
    "type" varchar(50)   NOT NULL,
    "comment" text   NOT NULL,
    "date" datetime   NOT NULL,
    CONSTRAINT "pk_problem_logs" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "helper_category" (
    "project_id" int   NOT NULL,
    "helper_id" int   NOT NULL,
    "category_id" int   NOT NULL
);

CREATE TABLE "category" (
    "id" int   NOT NULL,
    "project_id" int   NOT NULL,
    "name" varchar(50)   NOT NULL,
    "description" (text)   NOT NULL,
    CONSTRAINT "pk_category" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "problem_category" (
    "problem_id" int   NOT NULL,
    "category_id" int   NOT NULL
);

-- Free plan table limit reached. SUBSCRIBE for more.



ALTER TABLE "organization" ADD CONSTRAINT "fk_organization_org_owner_id" FOREIGN KEY("org_owner_id")
REFERENCES "user" ("id");

ALTER TABLE "project" ADD CONSTRAINT "fk_project_project_owner_id" FOREIGN KEY("project_owner_id")
REFERENCES "user" ("id");

ALTER TABLE "project" ADD CONSTRAINT "fk_project_organization_id" FOREIGN KEY("organization_id")
REFERENCES "organization" ("id");

ALTER TABLE "user_project" ADD CONSTRAINT "fk_user_project_user_id" FOREIGN KEY("user_id")
REFERENCES "user" ("id");

ALTER TABLE "user_project" ADD CONSTRAINT "fk_user_project_project_id" FOREIGN KEY("project_id")
REFERENCES "project" ("id");

ALTER TABLE "user_project" ADD CONSTRAINT "fk_user_project_role_id" FOREIGN KEY("role_id")
REFERENCES "role" ("id");

ALTER TABLE "role" ADD CONSTRAINT "fk_role_project_id" FOREIGN KEY("project_id")
REFERENCES "project" ("id");

ALTER TABLE "problem" ADD CONSTRAINT "fk_problem_user_id" FOREIGN KEY("user_id")
REFERENCES "user" ("id");

ALTER TABLE "problem" ADD CONSTRAINT "fk_problem_project_id" FOREIGN KEY("project_id")
REFERENCES "project" ("id");

ALTER TABLE "problem" ADD CONSTRAINT "fk_problem_helper_id" FOREIGN KEY("helper_id")
REFERENCES "user" ("id");

ALTER TABLE "problem_logs" ADD CONSTRAINT "fk_problem_logs_problem_id" FOREIGN KEY("problem_id")
REFERENCES "problem" ("id");

ALTER TABLE "problem_logs" ADD CONSTRAINT "fk_problem_logs_person_id" FOREIGN KEY("person_id")
REFERENCES "user" ("id");

ALTER TABLE "helper_category" ADD CONSTRAINT "fk_helper_category_project_id" FOREIGN KEY("project_id")
REFERENCES "project" ("id");

ALTER TABLE "helper_category" ADD CONSTRAINT "fk_helper_category_helper_id" FOREIGN KEY("helper_id")
REFERENCES "user" ("id");

ALTER TABLE "helper_category" ADD CONSTRAINT "fk_helper_category_category_id" FOREIGN KEY("category_id")
REFERENCES "category" ("id");

ALTER TABLE "category" ADD CONSTRAINT "fk_category_project_id" FOREIGN KEY("project_id")
REFERENCES "project" ("id");

ALTER TABLE "problem_category" ADD CONSTRAINT "fk_problem_category_problem_id" FOREIGN KEY("problem_id")
REFERENCES "problem" ("id");

ALTER TABLE "problem_category" ADD CONSTRAINT "fk_problem_category_category_id" FOREIGN KEY("category_id")
REFERENCES "category" ("id");

-- Free plan table limit reached. SUBSCRIBE for more.



-- Free plan table limit reached. SUBSCRIBE for more.




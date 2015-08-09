/*
 SQL script to add constrain and uniqueness on the contrib.auth User model.
 */

ALTER TABLE auth_user ADD UNIQUE (email);
CREATE UNIQUE INDEX auth_user_email_unique ON auth_user (email);

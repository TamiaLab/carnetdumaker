# TODO list for the CarnetDuMaker project

## ASAP

- More testing of code
- Code review (included .po files)

- The current HTML rendering code is more than broken. Need to be replaced with the new PySkCode engine.

## Text rendering engine

- Support smiley and cosmetics replacement
- Return extra information (headers hierarchy, footnotes, etc) as JSON

## Mailing

- Async mailer app (using CRON and management command)
- Async notification routine (using Celery)

## Cross publication

- Publication on Twitter / Facebook / Google+ for blog article
- Newsletter (by mail) for blog article

- Publication on Twitter / Facebook / Google+ for announcements
- Newsletter (by mail) for announcements

## Blog app

- Admin view to restore an article revision
- File attachments for blog article
- Handle pub_date modification of article with related forum thread
- "Report mistake" feature for blog article
- Blog article "get_short_content" helper
- Blog author article list and feed
- Blog use_count on tag for tag cloud size

## Search engine

- Integration search engine (using Haystack with Xapian)

## Bug tracker

- Icon "subscribed", "has post in", "unread" for all issue tickets
- Edit comments feature in bug tracker
- Delete comments feature in bug tracker

## Forum app

- Forum/thread reader tracker
- Forum post edit history (with revision like article for legal purposes)
- Icon "subscribed", "has post in", "unread" for all forum threads
- Forum threads/posts per author views and feeds
- Forum unread threads views
- Forum last_thread last_post post_count, thread_count, view_count, download_count (attachement)
- Detect reply during reply writing (forum)
- Display warning when posting on old topics

## Accounts app

- Limit HTMl tag allowed in user biography, signature and posts (with user permissions)

## Wish

- Warning/ban user
- Internal note system linked with user account

- Stats app
- Badge app
- Membership app
- Shop app
- Billing app
- Payment app

- Idea submission with vote app
- Blog article in progress with planning and status app (mini project management app)

## Work in progress

- Contact form app

## API

- Better HTML preview API with per-app (maybe per-user) limitations 
- API check if login JSON callback (to avoid data loose on submit with POST forms)

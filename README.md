
Runs on
http://localhost:9090

IMPORTANT!!!!!!!!!
To create the first table:
go to http://localhost:9090/tableInitializer

To **POST** - Create New Listing
'http://localhost:9090/api/listings/add_new_listing'

To queries all listings in the system:
  Gets all listings
  http://localhost:9090/api/listings/get

  To gt active listings:
    specify http://localhost:9090/api/listings/get?active=1 to get active listings

  To get paginated listings:
    specify http://localhost:9090/api/listings/get?length=<length>&page=<page>

  If no specifications are listed, should return all queries

To truncate a table:
  http://localhost:9090/api/listings/delete_all_listings

To get info for a single listing:
  http://localhost:9090/api/listings/<id> with get heade will return specific query

To Change info for a single listing http://localhost:9090/api/listings/<id>   specify 'PUT' and 'DELETE' for delete

Thanks very much for this opportunity I had a fun time doing it!

select url, location, test.http_requests.id
from test.rootid2 cross join test.pages cross join test.http_requests 
where test.rootid2.id = test.http_requests.page_id and test.rootid2.root_id = test.pages.id;

select value, third_domain
from test.thirdParty2 cross join test.http_request_headers
where test.thirdParty2.requestID = test.http_request_headers.http_request_id and
      test.http_request_headers.name = “cookie"
      order by third_domain;

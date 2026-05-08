when testing out api call, because of the spacing in the job description we get 
{
  "detail": [
    {
      "type": "json_invalid",
      "loc": [
        "body",
        40
      ],
      "msg": "JSON decode error",
      "input": {},
      "ctx": {
        "error": "Invalid control character at"
      }
    }
  ]
}
Response headers

so in order for people to copy the description in and paste, we need to add middleware that will resolve this. Check out JSONSanitizerMiddleware.



when setting alembic i had to drop tables  first time aroubd cause i had data
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS alembic_version;

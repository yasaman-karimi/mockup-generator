This is a Django REST Framework project that generates T-shirt mockups with custom text in four colors (yellow, black, white, and blue). It uses Celery and Redis to generate the images in the background and stores image paths in the database.

## Models
I used two models in this project:

MockupJob
This model is used to save user requests for Celery jobs.

Mockup
This model is used to save the created mockup images in the database.

## Endpoints
1. GenerateMockupView - POST api/v1/mockups/generate/

This endpoint first checks if the user is authenticated. It then creates a new mockup job based on the provided text, color, and font, and passes the job ID to the Celery task generate_mockups_task.

Celery Task Explanation:
This Celery task creates T-shirt mockup images for a given job. It marks the job as started, loads a base shirt image for each color, writes the job’s text on it, saves the resulting PNG files, and creates database entries for each mockup.
If all goes well, the job status becomes “SUCCESS”. If any error occurs, it’s marked as “FAILURE”.

Helper Functions Used:

1. _hex_to_rgb : converts a hex color code like #FFAA00 into an (R, G, B) tuple of integers.

2. _load_font attempts : to load a TrueType font from the project’s assets/fonts directory or from common system fonts, falling back to the default Pillow font if none are found.

3. _load_base_image : loads a T-shirt image of the requested color from the assets/tshirts folder; if no such file exists, it creates a solid-color image as a simple colored background.

4. _draw_centered_text : draws the given text in the center of the image using the provided font and color, calculating its position precisely so that it appears evenly aligned.

At the end, it returns the ID that Celery made for the task and saves it in the database. The generate function then returns:
{
    "task_id": task.id,
    "status": "PENDING",
    "message": "Image generation has started"
}

2. TaskStatusView - GET api/v1/tasks/{task_id}/

This class allows authenticated users to check the progress of a background task (Celery job).

When someone sends a GET request with a task_id, it first looks for a MockupJob in the database that matches the given task and belongs to the same user. Then it checks the current status of the Celery task using AsyncResult(task_id). If the Celery system doesn’t return a state, it uses the job’s saved status instead.

If the task is finished successfully (status “SUCCESS”), it collects all the mockup images that were generated for that job. For each mockup, it builds a full image URL (so it can be opened in the browser) and includes the creation time in ISO format.

Finally, it returns a JSON response containing:

 {
      "image_url": "http://127.0.0.1:8000/media/mockups/job3_black.png",
      "created_at": "2025-11-03T08:51:34.240880Z"
  }

3. MockupListView - GET api/mockups/

This class provides an API endpoint that lists all mockups created by the logged-in user.

It inherits from ListAPIView, which automatically handles GET requests and returns a list of items. Only signed-in users can access it. It uses MockupSerializer to convert each mockup object into JSON format for the response.

The get_queryset method defines which mockups should be shown: it fetches all Mockup records that belong to the current user (job__user=self.request.user). It also orders them by creation time (newest first) and uses select_related("job") to load related mockups efficiently in one query.

Finally, get_serializer_context is used to pass extra information — in this case, the current HTTP request — from the view to the serializer. The serializer then uses that request inside get_image_url to build a full, absolute link for each image instead of returning only a relative file path. This ensures that the API response includes complete URLs (like https://example.com/media/...) so that front-end clients can display the images correctly.

it returns a JSON response containing:
{
      "id": 2,
      "text": "Hello World",
      "image_url": "http://127.0.0.1:8000/media/mockups/job1_black.png",
      "font": "arial",
      "text_color": "#FFFFFF",
      "shirt_color": "black",
      "created_at": "2025-11-02T20:24:52.886297Z"
}
## Authentication (JWT)

I used Simple JWT for API authentication.
Clients first create an account, then obtain a pair of tokens: an access token (short-lived) and a refresh token (longer-lived). The access token is used to authenticate each request, and the refresh token is used to get a new access token when it expires.

1. RegisterView

This class handles user registration. It allows anyone to access it (AllowAny) since new users are not logged in yet.

When a POST request is sent with user data (like username, email, and password), it uses RegisterSerializer to check if the provided information is valid. If everything is correct, the serializer saves a new user in the database.

Finally, it returns the created user’s data as a response, along with the HTTP status code 201 Created, which means the account was successfully registered.

2. TokenObtainPairView

This class is provided by Simple JWT. It validates the username and password and returns an access token and a refresh token.

3. TokenRefreshView

This endpoint is used to exchange a valid refresh token for a new access token.

Clients send the access token in the Authorization header using the Bearer scheme on protected requests.
If the access token is missing, invalid, or expired, the API responds with an unauthorized error.

## Summary

This project shows how to combine:

Django REST Framework for building APIs

Celery and Redis for running background jobs

Pillow for image generation

Simple JWT for secure user authentication

It demonstrates how asynchronous processing and background tasks can be used to handle time-consuming operations like image creation without blocking the main application.

## Development Note

This project was initially created using Codex (OpenAI’s code generation tool) to help speed up the setup and structure.
After the first version was generated, I manually reviewed, edited, and refactored the code to fully understand how each part works — including the Celery integration, API logic, and image generation flow.

## Notes

- If a requested font is not found, falls back to a default font.
- If a base shirt image is not found, falls back to a solid color canvas.
- if the shirt color is not given by user, it creates all colors(yellow, black, white, and blue).
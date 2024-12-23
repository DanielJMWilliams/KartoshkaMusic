# KartoshkaMusic

A better looking display interface for Spotify.

I made this web-app because I did not like the Spotify UI displaying information about the current song. I like to see the album art so made this to display it in a more visually appealing way.

## Table of Contents

- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Development](#development)
- [Feature Wishlist](#feature-wishlist)
- [Known Issues](#known-issues)
- [Contact Information](#contact-information)

## Screenshots

![Image](/images/kartoshka_music.jpeg)

## Deployment

The aws configuration is defined with terraform. Pushing or completing a PR into the `deploy` branch will trigger a GitHub action that will deploy the code to https://kmusic.danielspyros.com/.

### Terraform in a docker container

1. Setup the terraform container.

e.g.
``docker run -dit --name terraform-container -v C:\Users\danca\Documents\projects\KartoshkaMusic\terraform:/terraform hashicorp/terraform:latest console``
Note: you will need to replace the path with the path to that terraform folder on your computer.

2. Set environment variables in terraform docker container. Obtain these from the aws console.
`export AWS_SECRET_ACCESS_KEY=xyz`
`export AWS_ACCESS_KEY_ID=xyz`

3. `terraform plan`

4. `terraform apply`

## Development


### Run with docker compose.
1. Setup `secrets.env` file. Use `secrets.example.env` as a template.
2. Docker compose.

`docker compose up -d --build`


### Run locally in virtual enviroment
1. Create Virtual Environment

`python -m venv venv`

2. Activate virtual environment

`venv\Scripts\Activate.ps1` 

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set Environment Variables
    - `$env:DJANGO_SETTINGS_MODULE="kmusic.settings"`
    - `$env:SPOTIFY_CLIENT_SECRET=""`
    - `$env:SPOTIFY_CLIENT_ID=""`
    - `$env:SPOTIFY_REDIRECT_URI="http://127.0.0.1:8000/callback" `
    - `$env:DEBUG="true"`

Spotify Client ID and Client Secret can be obtained here: https://developer.spotify.com/dashboard/.

5. Run server

`python manage.py runserver`

## Feature Wishlist

A list of ideas and features that may be considered for future development.

- Chaining songs in playlists

Ideas:

- grey song progess bar fills up
- hover over album to enlarge and get info
- click mini album to remove from queue?
- When playing multiple songs from one album consecutively, add number to mini album to indicate how many have already played. hovering over shows which songs in what order

## Known Issues
- album art too big for small screen
- pause icon not central
- background band photo needs height to be increased to 100% of main section

## Contact Information
Contact me on LinkedIn: www.linkedin.com/in/daniel-williams-5a74a71b0

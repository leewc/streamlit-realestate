This is a proof of concept where I learnt how to use Poetry to manage dependencies, Streamlit to visualize and display data, and Docker to containerize, and leverage a docker compose file to 'deploy'.

The (admittedly ugly) code is in `re.py`, and the data is fetched from Realtor.com via the intuitive [Homeharvest library](https://github.com/Bunsly/HomeHarvest) provided by Bunsly to scrape data.

## Demo

Demo is hosted at https://realestate.sjc.leewc.com/ (might be down at anytime, I make no guarantees of this proof of concept being available).

Video Demo

[streamlit-re-demo.webm](https://github.com/user-attachments/assets/dd33cdc3-b8cb-4cc7-a99e-0efbc039e32f)


## Without Docker

Running without docker is as simple as `poetry install`, activating the env, and then `streamlit run streamlit_realestate/re.py`. Tested on Python 3.11.

## With Docker

We leverage a multi-stage build to reduce image size.

```
git clone git@github.com:leewc/streamlit-realestate.git
cd streamlit-realestate
docker build -t streamlit .   
docker run -p 8501:8501 streamlit
```

## With docker compose (assuming Traefik is used)

```
docker compose up
```

Note you will have to change the traefik labels to fit your setup.

What is not not immediately intuitive is the healthcheck. If we leave the healthcheck as localhost, Traefik filters it out as 'Filtering unhealthy or starting container'. If we add a healthcheck in docker-compose.yaml, we have to expose the port `8501`. Hence, the best path forward might be to just omit the container level healthcheck and do the healthcheck on Traefik instead.

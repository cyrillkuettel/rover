# Rover Front-and Backend

## Website to display status information of robot. 


### Feature List
- [x] Websocket endpoint for low-latency bidirectional coummunication
- [x] Dynamically display status information
- [X] Display pictures, updated by ![App](https://github.com/cyrillkuettel/ecstatic-pilot)
- [x] Timer, fetch Timestamp from device
- [X] Switch between tabs
- [x] nginx running in docker
- [ ] Specify species and similarity of plants.
- [ ] species -> API
- [ ] Show Error messages, color code it
- [ ] image processing: image comparision algorithm
- [ ] Show Map based on GPS in phone





### various Notes on Unvicorn
Remember to exclude the --reload uvicorn option in production. The --reload option consumes much more resources, is more unstable, etc
Try to read the gunicorn.conf file in docker container. 

In Docker you can add --restart option to restart server if it crashes.


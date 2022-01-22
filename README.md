# Rover Front-and Backend

## Website to display status information of robot. 


### Feature List
- [x] Websocket endpoint for low-latency bidirectional coummunication
- [x] Dynamically display status information
- [X] Display pictures, updated by App (ecstatic pilot)
- [x] start accurate Time based on timestamr. (Also implemented with weboscket)
- [X] Switch between tabs
- [ ] nginx running in docker
- [ ] Show path (geographical) based on GPS with 
- [ ] Specify location of plant pot in row at the end
- [ ] Show Error messages, color code it
- [ ] image processing with high-performance Server? )





### various Notes
Remember to exclude the --reload uvicorn option in production. The --reload option consumes much more resources, is more unstable, etc
Try to read the gunicorn.conf file in docker container. 

In Docker you can add --restart option to restart server if it crashes.


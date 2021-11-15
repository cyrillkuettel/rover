# Rover Front-and Backend

## Website to display status information of robot. 


### Feature List
- [x] Websocket endpoint for low-latency bidirectional coummunication
- [x] Dynamically display status information
- [x] Show Error messages, color code it
- [x] start accurate Timer. (Also implemented with weboscket)
- [ ] Display pictures
- [ ] Show path (geographical) based on GPS with 
- [ ] Specify location of plant pot in row at the end
- [ ] image processing with high-performance Server? Of course, with massive parallelism. (If still time, this would be very interesting. Latency may be an issue, because of the size of the image )





### various Notes
Remember to exclude the --reload uvicorn option in production. The --reload option consumes much more resources, is more unstable, etc
Try to read the gunicorn.conf file in docker container. 

In Docker you can add --restart option to restart server if it crashes.


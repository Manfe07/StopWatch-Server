
export class FinishCam {
    constructor() {
        this.enabled = false;
        this.width = 1280; // We will scale the photo width to this
        this.height = 0; // This will be computed based on the input stream
        this.photos = [null, null, null, null];
        // |streaming| indicates whether or not we're currently streaming
        // video from the camera. Obviously, we start at false.

        this.streaming = false;

        // The various HTML elements we need to configure or control. These
        // will be set by the startup() function.

        this.video = null;
        this.canvas = null;
        this.startbutton = null;

    }



    startup() {
        this.enabled = true;
        this.video = document.getElementById("video");
        this.canvas = document.getElementById("canvas");
        this.startbutton = document.getElementById("startbutton");

        navigator.mediaDevices
            .getUserMedia({
                audio: false, video: {
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                    //width: { ideal: 3840 },
                    //height: { ideal: 2160 },
                    frameRate: { ideal: 60 },
                },
            })
            .then((stream) => {
                this.video.srcObject = stream;
                this.video.play();
            })
            .catch((err) => {
                console.error(`An error occurred: ${err}`);
                return false;
            });

        this.video.addEventListener(
            "canplay",
            (ev) => {
                if (!this.streaming) {
                    if (this.video.videoWidth) {
                        this.width = this.video.videoWidth;
                    }

                    if (this.video.videoHeight) {
                        this.height = this.video.videoHeight;
                    }
                    else {
                        this.height = this.video.videoHeight / (this.video.videoWidth / this.width);
                    }


                    // Firefox currently has a bug where the height can't be read from
                    // the video, so we will make assumptions if this happens.

                    if (isNaN(this.height)) {
                        this.height = this.width / (4 / 3);
                    }

                    this.video.setAttribute("width", this.video.videoWidth);
                    this.video.setAttribute("height", this.video.videoHeight);
                    this.canvas.setAttribute("width", this.video.videoWidth);
                    this.canvas.setAttribute("height", this.video.videoHeight);
                    this.streaming = true;
                }
            },
            false,
        );

        this.startbutton.addEventListener(
            "click",
            (ev) => {
                this.takePicture(0);
                ev.preventDefault();
            },
            false,
        );

        this.clearphoto();
        return true;
    }

    // Fill the photo with an indication that none has been
    // captured.

    clearphoto() {
        const context = this.canvas.getContext("2d");
        context.fillStyle = "#AAA";
        context.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const data = this.canvas.toDataURL("image/png");
    }

    // Capture a photo by fetching the current contents of the video
    // and drawing it into a canvas, then converting that to a PNG
    // format data URL. By drawing it on an offscreen canvas and then
    // drawing that to the screen, we can change its size and/or apply
    // other changes before drawing it.

    //async takePicture(lane) {
    takePicture(lane) {
        let enabled = this.enabled
        //return new Promise(function(success, failed){
        if (enabled) {
            console.debug("Video:", this.video);
            console.debug("Height", this.video.videoHeight);
            console.debug("Width", this.video.videoWidth);

            //photo.setAttribute("width", this.video.videoWidth);
            //photo.setAttribute("height", this.video.videoHeight);

            const context = this.canvas.getContext("2d");
            if (this.width && this.height) {
                this.canvas.width = this.width;
                this.canvas.height = this.height;
                context.drawImage(this.video, 0, 0, this.width, this.height);
                console.log("PictueFinished. Lane", lane);
                const data = canvas.toDataURL("image/png");
                this.photos[lane] = data;
            } else {
                this.clearphoto();
            }
            //        success();
            return true;
        }

        else {
            //        failed();
            return false;
        }
        //});
    }

    // Set up our event listener to run the startup process
    // once loading is complete.
}


export var finishCam = new FinishCam();
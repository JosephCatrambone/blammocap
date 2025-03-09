import './style.css'
import { Frame, Detection } from './datamodels.ts';
//import { setupCounter } from './counter.ts'
//import { AR } from "./js-aruco2/src/aruco.js";
// @ts-ignore
import { AR } from './js-aruco2/src/aruco.ts';

let remoteName: HTMLInputElement;
let cameraName: HTMLInputElement;
let detectorSelector: HTMLSelectElement;
let videoSourceSelector: HTMLSelectElement;
let videoElement: HTMLVideoElement;
let canvasElement: HTMLCanvasElement;
let context: CanvasRenderingContext2D;
let imageData: ImageData;

// Image processing and detectors:
let socket: WebSocket = new WebSocket("ws://localhost:8765");
let detector: AR.Detector;


/*
class MainApp {
	// A hack to preserve the 'this' context so we can hammer requestAnimationFrame.
	update = () => void {

	}
}
*/

export function initApp(app: HTMLDivElement) {
	/*
	let counter = 0;
	const setCounter = (count: number) => {
		counter = count
		element.innerHTML = `count is ${counter}`
	}
	element.addEventListener('click', () => setCounter(counter + 1))
	setCounter(0);
	 */
  remoteName = document.createElement("input");
  remoteName.id = "remoteName";
  remoteName.name = "Remote Server Address";
  remoteName.type = "text";
  remoteName.value = "ws://localhost:8765"

	cameraName = document.createElement("input");
	cameraName.id = "cameraName";
	cameraName.name = "Camera Name Input";
	cameraName.type = "text";

	//const detectorSelector: HTMLSelectElement = document.createElement("select");
	detectorSelector = document.createElement("select");
	detectorSelector.id = 'fiducialSelector';
	detectorSelector.name = "AR Marker Type Selector";

	videoSourceSelector = document.createElement("select");
	videoSourceSelector.id = 'cameraSelector';
	videoSourceSelector.name = "Camera Selector";

	videoElement = document.createElement("video");
	videoElement.style.display = 'none'; // We only want to write video frames here, not show them.
	videoElement.id = 'videoPreview';
	videoElement.autoplay = true;
	videoElement.muted = true;
	// TODO: Make this adjustable?
	videoElement.width = 640;
	videoElement.height = 480;

	detector = new AR.Detector();
	canvasElement = document.createElement("canvas");
	canvasElement.width = videoElement.width;
	canvasElement.height = videoElement.height;

	configureCameraNameInput(cameraName);

	populateFiducialDetector(detectorSelector);

	populateCameraSelector(videoSourceSelector, videoElement).then(() => {
		let outputs = document.createElement("div");
		outputs.appendChild(videoElement);
		outputs.appendChild(canvasElement);

		let controls = document.createElement("div");
		controls.appendChild(remoteName);
		controls.appendChild(cameraName);
		controls.appendChild(detectorSelector);
		controls.appendChild(videoSourceSelector);

		app.append(outputs);
		app.appendChild(controls);

		let ctx = canvasElement.getContext('2d');
		if (ctx !== null) {
			context = ctx;
		}
	});
	//app.innerHTML = `${videoPreview}${dropdownMenu}`;
}


function configureCameraNameInput(nameInput: HTMLInputElement) {
	nameInput.value = `Camera${Math.random()}`;
}


function configureRemoteInput(inElem: HTMLInputElement) {
  inElem.onchange = null;
  inElemn.onchange = (evt) => {
    let remote = evt.target!.value;
    socket = new WebSocket(remote);    
    console.log(`Opening connection to ${remote}`);
  }
}


function populateFiducialDetector(selector: HTMLSelectElement) {
	selector.onchange = null;
	selector.onchange = (evt) => {
		
	}

	// For each possible detector...
	
}


async function populateCameraSelector(selector: HTMLSelectElement, videoOut: HTMLVideoElement) {
	selector.onchange = null;
	selector.onchange = (e) => {
		//onDeviceChanged(e.target!.value);
		connectCamera(videoOut, e.target!.value);
	}

	// Add the empty default:
	const noCamera = document.createElement("option");
	noCamera.label = "Select Camera:";
	noCamera.value = "";
	selector.appendChild(noCamera);

	// Add the actual camera elements.
	// We need the first getUserMedia to force permissions for video devices.
	await navigator.mediaDevices.getUserMedia({video: true, audio: false});
	navigator.mediaDevices.enumerateDevices().then((devices) => {
		//audioList.textContent = ""; videoList.textContent = "";
		devices.forEach((device) => {
			// @ts-ignore
			//const [kind, type, direction] = device.kind.match(/(\w+)(input|output)/i);
			if (device.kind == "videoinput") {
				const cameraOption = document.createElement('option');
				cameraOption.label = device.label;
				cameraOption.value = device.deviceId;
				selector.appendChild(cameraOption);
			}
		});
	});
}

function connectCamera(videoPreview: HTMLVideoElement, deviceId: string) {
	// If deviceID is null and there's an existing stream we close it.
	// This also serves to close the tick function.
	if (deviceId == "" || deviceId == null) {
		videoPreview.srcObject = null;
		return;
	}

	const constraints = { // This will be repopulated by the getUserMedia stream.
		video: {
			deviceId: deviceId,
		},
		audio: false, // Don't need this.
	}
	navigator
		.mediaDevices
		.getUserMedia(constraints)
		.then(stream => {
			//const videoTracks = stream.getVideoTracks();
			stream.onremovetrack = () => {
				console.log("Stream ended");
			};
			videoPreview.srcObject = stream;
			requestAnimationFrame(tick);
		})
		.catch(error => {
			if (error.name === "OverconstrainedError") {
				console.error(`The resolution ${constraints.video.width?.exact}x${constraints.video.height.exact} px is not supported by your device.`,);
			} else if (error.name === "NotAllowedError") {
				console.error("This page needs permission to read from your webcam.",);
			} else {
				console.error(`getUserMedia error: ${error.name}`, error);
			}
		})
	// <option value="first">First Value</option>
}

export function tick() {
	if (videoElement.srcObject === null) {
		return;
	}
	requestAnimationFrame(tick);

	context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
	let timestamp = Date.now(); // As soon as we capture it.
	imageData = context.getImageData(0, 0, canvasElement.width, canvasElement.height);

	if (detector != null && socket != null) {
		// Send frames immediately or send them as a worker?
		var markers = detector.detect(imageData);
		if (socket.readyState == WebSocket.OPEN) {
			let f: Frame = new Frame();
			f.camera_name = cameraName.value;
			f.timestamp = timestamp;
			f.markers = [];
			for (let i = 0; i < markers.length; i++) {
				// This is all in the name of a conversion.  Would be nice to have a better/faster way to do it.
				let m: Detection = {
					id: markers[i].id,
					hamming_distance: markers[i].hammingDistance,
					corners: [
						markers[i].corners[0],
						markers[i].corners[1],
						markers[i].corners[2],
						markers[i].corners[3],
					]
				}
				f.markers.push(m);
			}
			socket.send(JSON.stringify(f));
		} else {
		  console.log(markers);
		}
	}
	// Render debug?
}


initApp(document.querySelector<HTMLDivElement>('#app')!)

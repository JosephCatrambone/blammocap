let video;
let bodyPose;
let socket = new WebSocket("ws://localhost:8765");
let poses = [];

function preload() {
	// let bodypose = ml5.bodyPose(?model, ?options, ?callback);
	/*
	{
		modelType: "MULTIPOSE_LIGHTNING", // "MULTIPOSE_LIGHTNING", "SINGLEPOSE_LIGHTNING", or "SINGLEPOSE_THUNDER".
		enableSmoothing: true,
		minPoseScore: 0.25,
		multiPoseMaxDimension: 256,
		enableTracking: true,
		trackerType: "boundingBox", // "keypoint" or "boundingBox"
		trackerConfig: {},
		modelUrl: undefined,
		flipped: false
	}
	 */
	bodyPose = ml5.bodyPose()

}

function setup() {
	createCanvas(640, 480);

	// Create the video and hide it
	video = createCapture(VIDEO);
	video.size(640, 480);
	video.hide();

	bodyPose.detectStart(video, onGetPoses);
}

function draw() {}

// Callback function for when the model returns pose data
function onGetPoses(results, errors) {
    // Store the model's results in a global variable
    poses = results;

	/*
	BodyPose's MoveNet model predicts a set of 17 keypoints:
	Nose, Left Eye, Right Eye, Left Ear, Right Ear, Left Shoulder, Right Shoulder, Left Elbow, Right Elbow, Left Wrist, Right Wrist, Left Hip, Right Hip, Left Knee, Right Knee, Left Ankle, Right Ankle

	BodyPose's BlazePose model predicts a set of 33 keypoints:
	Nose, Left Eye Inner, Left Eye, Left Eye Outer, Right Eye Inner, Right Eye, Right Eye Outer, Left Ear, Right Ear, Mouth Left, Mouth Right, Left Shoulder, Right Shoulder, Left Elbow, Right Elbow, Left Wrist, Right Wrist, Left Pinky, Right Pinky, Left Index, Right Index, Left Thumb, Right Thumb, Left Hip, Right Hip, Left Knee, Right Knee, Left Ankle, Right Ankle, Left Heel, Right Heel, Left Foot Index, Right Foot Index, Body Center, Forehead, Left Thumb, Left Hand, Right Thumb, Right Hand
	 */

	if (socket.readyState === WebSocket.OPEN) {

	}
	/*
	[
		{
			box: { width, height, xMax, xMin, yMax, yMin },
			id: 1,
			keypoints: [{ x, y, confidence, name }, ...],
			left_ankle: { x, y, confidence },
			left_ear: { x, y, confidence },
			left_elbow: { x, y, confidence },
			...
			confidence: 0.28,
		},
	*/
}
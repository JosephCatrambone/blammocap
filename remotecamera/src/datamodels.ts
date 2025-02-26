// generated:
// filename:  protocol.json
// timestamp: 2025-02-25T19:45:38+00:00

export class Point {
    x: number = 0;
    y: number = 0;
}

export class Detection {
    id: number  = 0;
    hamming_distance: number  = 0;
    corners: Point[] = [];
}

export class Frame {
    camera_name: string = "";
    timestamp: number = 0;
    markers: Detection[] = [];
}

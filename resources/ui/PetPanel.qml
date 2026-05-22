import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 200
    height: 200

    property real petX: 100
    property real petY: 100
    property string petState: "idle"
    property bool facingRight: true
    property string bubbleText: ""
    property bool bubbleVisible: false

    property real animFrame: 0
    property real bodyBob: 0
    property real tailAngle: 0
    property real eyeScale: 1.0
    property real legAngle: 0
    property real sleepZ: 0

    Timer {
        interval: 33
        running: true
        repeat: true
        onTriggered: {
            animFrame = (animFrame + 1) % 360
            var t = animFrame * 0.01745

            if (petState === "idle") {
                bodyBob = Math.sin(t * 0.5) * 3
                tailAngle = Math.sin(t * 0.67) * 0.26
                legAngle = 0
            } else if (petState === "walk") {
                bodyBob = Math.sin(t * 4) * 2
                tailAngle = Math.sin(t * 5) * 0.4
                legAngle = Math.sin(t * 4)
            } else if (petState === "jump") {
                var jumpProgress = (animFrame % 18) / 18
                bodyBob = -Math.sin(jumpProgress * Math.PI) * 40
                eyeScale = 1 + Math.sin(jumpProgress * Math.PI * 2) * 0.3
                tailAngle = Math.sin(t * 2) * 0.3
                legAngle = Math.sin(t * 3)
            } else if (petState === "sleep") {
                bodyBob = 5
                tailAngle = 0
                legAngle = 0
                sleepZ = (sleepZ + 0.02) % 1
            } else if (petState === "chase") {
                bodyBob = Math.sin(t * 5) * 2
                tailAngle = Math.sin(t * 6) * 0.5
                legAngle = Math.sin(t * 6)
            } else if (petState === "drag") {
                bodyBob = -10
                tailAngle = Math.sin(t * 3) * 0.5
                legAngle = Math.sin(t * 5)
            } else if (petState === "hang") {
                bodyBob = -5
                tailAngle = 0
                legAngle = 0
            }

            canvas.requestPaint()
        }
    }

    Canvas {
        id: canvas
        anchors.fill: parent

        onPaint: {
            var ctx = canvas.getContext("2d")
            ctx.clearRect(0, 0, canvas.width, canvas.height)

            var cx = petX
            var cy = petY + bodyBob
            var scale = 1.0

            ctx.save()
            if (!facingRight) {
                ctx.translate(canvas.width, 0)
                ctx.scale(-1, 1)
                cx = canvas.width - petX
            }

            // tail stroke
            ctx.strokeStyle = "#1a1a1a"
            ctx.lineWidth = 6
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.moveTo(cx - 12, cy + 15)
            var tailTipX = cx - 12 + Math.sin(tailAngle) * 30
            var tailTipY = cy + 15 + Math.cos(tailAngle) * 10 - 15
            ctx.quadraticCurveTo(cx - 20, cy + 5, tailTipX, tailTipY)
            ctx.stroke()

            // body
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.ellipse(cx, cy + 5, 22, 20)
            ctx.fill()

            // legs
            var legSwing = legAngle * 0.3
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.ellipse(cx - 10 + legSwing * 5, cy + 22, 6, 8)
            ctx.fill()
            ctx.beginPath()
            ctx.ellipse(cx + 10 - legSwing * 5, cy + 22, 6, 8)
            ctx.fill()
            ctx.beginPath()
            ctx.ellipse(cx - 14 + legSwing * 3, cy + 20, 4, 6)
            ctx.fill()
            ctx.beginPath()
            ctx.ellipse(cx + 14 - legSwing * 3, cy + 20, 4, 6)
            ctx.fill()

            // head
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.arc(cx, cy - 10, 18, 0, Math.PI * 2)
            ctx.fill()

            // ears
            ctx.beginPath()
            ctx.moveTo(cx - 14, cy - 18)
            ctx.lineTo(cx - 20, cy - 35)
            ctx.lineTo(cx - 6, cy - 22)
            ctx.closePath()
            ctx.fill()
            ctx.beginPath()
            ctx.moveTo(cx + 14, cy - 18)
            ctx.lineTo(cx + 20, cy - 35)
            ctx.lineTo(cx + 6, cy - 22)
            ctx.closePath()
            ctx.fill()

            // inner ears
            ctx.fillStyle = "#2a2a2a"
            ctx.beginPath()
            ctx.moveTo(cx - 13, cy - 20)
            ctx.lineTo(cx - 17, cy - 31)
            ctx.lineTo(cx - 8, cy - 23)
            ctx.closePath()
            ctx.fill()
            ctx.beginPath()
            ctx.moveTo(cx + 13, cy - 20)
            ctx.lineTo(cx + 17, cy - 31)
            ctx.lineTo(cx + 8, cy - 23)
            ctx.closePath()
            ctx.fill()

            // eyes
            if (petState === "sleep") {
                ctx.strokeStyle = "#111111"
                ctx.lineWidth = 2
                ctx.beginPath()
                ctx.arc(cx - 8, cy - 8, 6, 0, Math.PI)
                ctx.stroke()
                ctx.beginPath()
                ctx.arc(cx + 8, cy - 8, 6, 0, Math.PI)
                ctx.stroke()
            } else {
                var eyeW = 7 * eyeScale
                var eyeH = 7 * eyeScale
                ctx.fillStyle = "#ffdd44"
                ctx.beginPath()
                ctx.ellipse(cx - 8, cy - 10, eyeW, eyeH)
                ctx.fill()
                ctx.beginPath()
                ctx.ellipse(cx + 8, cy - 10, eyeW, eyeH)
                ctx.fill()
                ctx.fillStyle = "#111111"
                ctx.beginPath()
                ctx.ellipse(cx - 7, cy - 9, 3, 4)
                ctx.fill()
                ctx.beginPath()
                ctx.ellipse(cx + 9, cy - 9, 3, 4)
                ctx.fill()
                ctx.fillStyle = "#ffffff"
                ctx.beginPath()
                ctx.arc(cx - 6, cy - 12, 1.5, 0, Math.PI * 2)
                ctx.fill()
                ctx.beginPath()
                ctx.arc(cx + 10, cy - 12, 1.5, 0, Math.PI * 2)
                ctx.fill()
            }

            // mouth
            if (petState === "jump" || petState === "drag") {
                ctx.fillStyle = "#e88"
                ctx.beginPath()
                ctx.arc(cx, cy - 2, 4, 0, Math.PI)
                ctx.fill()
            } else if (petState !== "sleep") {
                ctx.strokeStyle = "#111111"
                ctx.lineWidth = 1.5
                ctx.beginPath()
                ctx.arc(cx, cy - 4, 4, 0.2, Math.PI - 0.2)
                ctx.stroke()
            }

            // Zzz for sleep
            if (petState === "sleep") {
                ctx.fillStyle = "#888888"
                ctx.font = "12px sans-serif"
                var z = sleepZ
                if (z > 0) ctx.fillText("z", cx + 20, cy - 30)
                if (z > 0.3) ctx.fillText("z", cx + 28, cy - 40)
                if (z > 0.6) ctx.fillText("Z", cx + 36, cy - 50)
            }

            ctx.restore()
        }
    }

    // Speech bubble
    Rectangle {
        id: bubble
        visible: bubbleVisible && bubbleText.length > 0
        x: facingRight ? petX + 20 : petX - 20 - bubbleContent.width - 20
        y: petY - 50
        width: bubbleContent.width + 20
        height: bubbleContent.height + 12
        radius: 10
        color: "#ffffff"
        opacity: 0.92

        Text {
            id: bubbleContent
            anchors.centerIn: parent
            text: bubbleText
            font.pixelSize: 12
            color: "#333333"
        }

        Rectangle {
            x: facingRight ? 10 : parent.width - 30
            y: parent.height - 4
            width: 8
            height: 8
            rotation: 45
            color: parent.color
        }
    }
}

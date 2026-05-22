import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: parent ? parent.width : 800
    height: parent ? parent.height : 200

    property real petX: 100
    property real petY: 170
    property string petState: "walk"
    property bool facingRight: true
    property string bubbleText: ""
    property bool bubbleVisible: false

    property real animFrame: 0
    property real bobY: 0
    property real tiltAngle: 0
    property real scaleX: 1.0
    property real scaleY: 1.0
    property real petOpacity: 1.0
    property real sleepZ: 0

    Timer {
        interval: 33
        running: true
        repeat: true
        onTriggered: {
            animFrame = (animFrame + 1) % 360
            var t = animFrame * 0.01745

            if (petState === "idle") {
                bobY = Math.sin(t * 0.5) * 3
                tiltAngle = Math.sin(t * 0.3)
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 1.0
            } else if (petState === "walk") {
                bobY = Math.sin(t * 4) * 3
                tiltAngle = Math.sin(t * 2) * 2
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 1.0
            } else if (petState === "jump") {
                var jumpProgress = (animFrame % 18) / 18
                bobY = -Math.sin(jumpProgress * Math.PI) * 50
                tiltAngle = 0
                var sq = Math.sin(jumpProgress * Math.PI * 2)
                scaleX = 1.0 + sq * 0.08
                scaleY = 1.0 - sq * 0.08
                petOpacity = 1.0
            } else if (petState === "sleep") {
                bobY = 3
                tiltAngle = 3
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 0.8
                sleepZ = (sleepZ + 0.02) % 1
            } else if (petState === "chase") {
                bobY = Math.sin(t * 6) * 2
                tiltAngle = 5
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 1.0
            } else if (petState === "drag") {
                bobY = -5
                tiltAngle = Math.sin(t * 2) * 5
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 1.0
            } else if (petState === "hang") {
                bobY = 0
                tiltAngle = -10
                scaleX = 1.0; scaleY = 1.0
                petOpacity = 0.7
            }
        }
    }

    Item {
        id: spriteContainer
        width: spriteImage.width
        height: spriteImage.height
        x: petX - width / 2
        y: petY - height / 2 + bobY
        opacity: petOpacity

        transform: Rotation {
            origin.x: spriteContainer.width / 2
            origin.y: spriteContainer.height / 2
            angle: tiltAngle
        }

        Image {
            id: spriteImage
            source: "../sprites/罗小黑.png"
            sourceSize.width: 80
            fillMode: Image.PreserveAspectFit
            smooth: true
            mirror: !facingRight
            anchors.centerIn: parent

            transform: Scale {
                origin.x: spriteImage.width / 2
                origin.y: spriteImage.height / 2
                xScale: scaleX
                yScale: scaleY
            }
        }
    }

    Text {
        id: zzzText
        visible: petState === "sleep"
        text: "Zzz"
        color: "#888888"
        font.pixelSize: 12
        x: facingRight ? petX + 25 : petX - 55
        y: petY - 45 + (sleepZ > 0.6 ? -10 : 0)
        opacity: sleepZ > 0.6 ? 0.6 : (sleepZ > 0.3 ? 0.8 : 1.0)
    }

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
        z: 10

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

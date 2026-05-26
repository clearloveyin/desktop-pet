import QtQuick 2.15

Item {
    id: root
    width: parent ? parent.width : 120
    height: parent ? parent.height : 120
    clip: true

    property string petState: "idle"
    property bool petThinking: petBridge.petThinking
    property string bubbleText: petBridge.bubbleText

    function gifForState(state) {
        switch(state) {
            case 'idle': return gifBaseUrl + '待机.gif';
            case 'walk': return gifBaseUrl + '奔跑.gif';
            case 'angry': return gifBaseUrl + '疲惫.gif';
            default: return gifBaseUrl + '待机.gif';
        }
    }

    AnimatedImage {
        anchors.centerIn: parent
        width: 80; height: 80
        fillMode: Image.PreserveAspectFit
        smooth: true
        source: gifBaseUrl + '思考.gif'
        playing: petThinking
        visible: petThinking
    }

    AnimatedImage {
        anchors.centerIn: parent
        width: 80; height: 80
        fillMode: Image.PreserveAspectFit
        smooth: true
        source: gifForState(petState)
        playing: !petThinking
        visible: !petThinking
    }

    Rectangle {
        id: bubble
        anchors.horizontalCenter: parent.horizontalCenter
        y: -8
        width: textItem.width + 16
        height: textItem.height + 16
        radius: 8
        color: "#ffffff"
        border.color: "#cccccc"
        border.width: 1
        visible: bubbleText !== ""
        opacity: bubbleText !== "" ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 150 } }

        Text {
            id: textItem
            text: bubbleText
            font.pixelSize: 12
            color: "#333333"
            anchors.centerIn: parent
        }
    }

    DropArea {
        anchors.fill: parent
        onEntered: {
            if (drag.hasUrls) {
                drag.accept()
                petBridge.petThinking = true
                petBridge.bubbleText = "给我的？"
            }
        }
        onExited: {
            petBridge.petThinking = false
            petBridge.bubbleText = ""
        }
        onDropped: {
            if (drop.hasUrls) {
                var paths = []
                for (var i = 0; i < drop.urls.length; i++) {
                    var urlStr = drop.urls[i].toString()
                    if (urlStr.indexOf('file://') === 0) {
                        urlStr = urlStr.slice(7)
                    }
                    paths.push(urlStr)
                }
                petBridge.filesDropped(paths)
                drop.accept()
            }
            petBridge.petThinking = false
            petBridge.bubbleText = ""
            petBridge.chatRequested()
        }
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        property int dragStartX: 0
        property int dragStartY: 0
        property bool wasDragged: false
        property bool dragging: false

        onPressed: function(mouse) {
            if (mouse.button !== Qt.LeftButton) return
            dragStartX = mouse.x
            dragStartY = mouse.y
            wasDragged = false
            dragging = true
        }

        onPositionChanged: function(mouse) {
            if (!dragging) return
            var dx = mouse.x - dragStartX
            var dy = mouse.y - dragStartY
            if (Math.abs(dx) + Math.abs(dy) > 5) {
                wasDragged = true
                petBridge.dragMoveRequested(dx, dy)
                dragStartX = mouse.x
                dragStartY = mouse.y
            }
        }

        onReleased: function(mouse) {
            if (!dragging) return
            dragging = false
            if (!wasDragged) {
                petBridge.clickRequested()
            }
        }

        onClicked: function(mouse) {
            if (mouse.button === Qt.RightButton) {
                petBridge.contextMenuRequested()
            }
        }
    }
}

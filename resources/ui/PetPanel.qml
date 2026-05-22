import QtQuick 2.15

Item {
    id: root
    width: parent ? parent.width : 120
    height: parent ? parent.height : 120

    property string petState: "idle"

    AnimatedImage {
        id: petAnim
        width: 80
        height: 80
        fillMode: Image.PreserveAspectFit
        smooth: true
        anchors.centerIn: parent

        source: petState === "idle" ? "../sprites/待机.gif" :
                petState === "walk" ? "../sprites/奔跑.gif" :
                "../sprites/疲惫.gif"
    }

    MouseArea {
        anchors.fill: parent
        onClicked: petBridge.clickRequested()
    }
}

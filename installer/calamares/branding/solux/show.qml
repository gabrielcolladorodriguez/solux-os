/* Solux OS — Presentación durante la instalación (Calamares) */
import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation

    Timer {
        interval: 6000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Rectangle {
            anchors.fill: parent
            color: "#0D0D1A"
            Text {
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                color: "#F97316"
                font.pixelSize: 28
                font.bold: true
                text: "Bienvenido a Solux OS\n\nSeguridad que renace contigo."
            }
        }
    }

    Slide {
        Rectangle {
            anchors.fill: parent
            color: "#0D0D1A"
            Text {
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                color: "#F1F5F9"
                font.pixelSize: 22
                text: "Cifrado LUKS de disco completo activado por defecto.\nTus datos protegidos incluso si pierdes el equipo."
            }
        }
    }

    Slide {
        Rectangle {
            anchors.fill: parent
            color: "#0D0D1A"
            Text {
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                color: "#3B82F6"
                font.pixelSize: 22
                text: "Miles de apps open source y el arsenal completo de Kali\nte esperan en la Solux Store."
            }
        }
    }
}

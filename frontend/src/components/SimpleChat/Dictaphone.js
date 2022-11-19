import React, {useEffect} from 'react'
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'
import {BiMicrophoneOff} from "react-icons/bi"
import {BsFillRecordCircleFill} from "react-icons/bs"
import {HiMicrophone} from "react-icons/hi"

import messagesStore from "../../stores/messagesStore"


const Dictaphone = () => {
  const {selectedChatText} = messagesStore
  const {transcript, listening, browserSupportsSpeechRecognition} = useSpeechRecognition()

  useEffect(() => {
    if (!listening && transcript) {
      if (selectedChatText) {
        messagesStore.addTextToSelectedChat(` ${transcript}`)
      } else {
        messagesStore.setSelectedChatText(transcript)
      }
    }
  }, [listening])

  if (!browserSupportsSpeechRecognition) {
    return (
      <span
        className="text-danger ms-1 mb-1 align-self-center fs-4"
        title="Ваш браузер не поддерживает распознавание голоса"
      >
        <BiMicrophoneOff/>
      </span>
    )
  }

  const startListening = e => {
    e.preventDefault()
    SpeechRecognition.startListening()
  }

  const stopListening = e => {
    e.preventDefault()
    SpeechRecognition.stopListening()
  }

 return (
    <div className="ms-1 mb-1 align-self-center fs-4">
      {
        listening
          ? <span
            className="text-danger"
            onClick={stopListening}
          >
            <BsFillRecordCircleFill/>
          </span>
          : <span
              className="text-primary"
              onClick={startListening}
          >
            <HiMicrophone/>
          </span>
      }
    </div>
  )
}
export default Dictaphone

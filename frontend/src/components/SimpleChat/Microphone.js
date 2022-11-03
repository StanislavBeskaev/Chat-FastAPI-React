import React, {useState, useEffect} from 'react'
import {HiMicrophone} from "react-icons/hi"
import {BsFillRecordCircleFill} from "react-icons/bs"

import messagesStore from "../../stores/messagesStore"

const Microphone = () => {
  const [isRecord, setIsRecord] = useState(false)
  const [recorder, setRecorder] = useState(null)

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognizer = new SpeechRecognition()
    // Ставим опцию, чтобы распознавание началось ещё до того, как пользователь закончит говорить
    recognizer.interimResults = true
    recognizer.lang = 'ru-Ru'
    console.log(recognizer)

    recognizer.onresult = event => {
      const result = event.results[event.resultIndex]
      if (result.isFinal) {
        const text = result[0].transcript
        messagesStore.addTextToSelectedChat(` ${text}`)
        recognizer.stop()
        setIsRecord(false)
      }
    }

    recognizer.onend = event => {
      setIsRecord(false)
    }
    setRecorder(recognizer)
  }, [])

  const startSpeechRecognition = () => {
    recorder.start()
    setIsRecord(true)
  }

  const stopSpeechRecognition = () => {
    recorder.stop()
    setIsRecord(false)
  }

  return (
    <div className="ms-1 mb-1 align-self-center fs-4">
      {
        isRecord
          ? <span
            className="text-danger"
            onClick={stopSpeechRecognition}
          >
            <BsFillRecordCircleFill/>
          </span>
          : <span
              className="text-primary"
              onClick={startSpeechRecognition}
          >
            <HiMicrophone/>
          </span>
      }
    </div>
  )
}

export default Microphone
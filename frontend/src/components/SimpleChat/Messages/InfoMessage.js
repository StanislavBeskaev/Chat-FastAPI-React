import React, {useEffect} from 'react'
import {useInView} from 'react-intersection-observer'
import messagesStore from '../../../stores/messagesStore'
import formatDate from '../../../utils/time'

const InfoMessage = ({message}) => {
  const {text, time} = message

  const { ref, inView, entry } = useInView({
    threshold: 1
  })

  useEffect(() => {
    if (!entry) return

    if (inView) {
      messagesStore.addMessageToInView(message)
    } else {
      messagesStore.deleteMessageFromInView(message)
    }
  }, [inView])

  return (
    <div
      ref={ref}
      id={message.message_id}
      className="p-1 align-self-center text-muted"
      style={{fontSize: 14}}
    >
      {formatDate(time)} {text}
    </div>
  )
}

export default InfoMessage
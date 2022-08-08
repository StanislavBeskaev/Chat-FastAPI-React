import React from 'react'
import {AiFillDownCircle} from 'react-icons/ai'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../../stores/messagesStore'


const ScrollButton = () => {
  const isLastMessageSeen = messagesStore.isSelectedChatLastMessageInView()

  const scrollToBottom = () => {
    const selectedChatLastMessage = document.getElementById(messagesStore.getSelectedChatLastMessageId())
    selectedChatLastMessage.scrollIntoView({behavior: 'smooth'})
  }

  return (
    <>
      {
        !isLastMessageSeen
          ? <span
              onClick={() => scrollToBottom()}
              style={{
                position: 'absolute',
                right: 25,
                bottom: 80,
                fontSize: 35,
                cursor: 'pointer',
                color: 'dodgerblue',
                opacity: 0.9
              }}
            >
              <AiFillDownCircle/>
            </span>
          : null
      }
    </>
  )
}

export default observer(ScrollButton)
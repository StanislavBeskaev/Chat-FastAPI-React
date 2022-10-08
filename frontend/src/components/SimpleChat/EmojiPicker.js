import React, {useState} from 'react'
import Picker from '@emoji-mart/react'
import data from '@emoji-mart/data'
import messagesStore from '../../stores/messagesStore'


const EmojiPicker = () => {
  const [show, setShow] = useState(false)

  const hidePicker = () => {
    setTimeout(() => setShow(false), 300)
  }

  const showPicker = () => {
    if (!show) setShow(true)
  }

  const addEmoji = e => {
    messagesStore.addTextToSelectedChat(e.native)
  }

  return (
    <>
      <div onMouseOver={showPicker} className="fs-3 ms-1 align-self-center">
        😉
      </div>
      {
        show
          ? <div
            onMouseOut={hidePicker}
            style={{position: "fixed", bottom: "55px", left: "26%"}}
            id="picker"
          >
            <Picker
              data={data}
              onEmojiSelect={addEmoji}
              locale="ru"
              previewPosition="top"
              theme="light"
            />
          </div>
          : null
      }
    </>
  )
}

export default EmojiPicker
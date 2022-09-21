import React, {useState} from 'react';
import {BiMessageAdd} from 'react-icons/bi'

import newChatModalStore from '../../stores/modals/newChatModalStore'

const INITIAL_COLOR = 'dodgerblue'
const HOVER_COLOR = 'rgb(49, 108, 244)'


const NewChatButton = () => {
  const [color, setColor] = useState(INITIAL_COLOR)

  return (
    <span
      style={{
        marginTop: -25,
        paddingRight: 5,
        fontSize: 50,
        cursor: 'pointer',
        color,
      }}
      title="Создать чат"
      onClick={() => newChatModalStore.open()}
      onMouseOver={() => setColor(HOVER_COLOR)}
      onMouseOut={() => setColor(INITIAL_COLOR)}
    >
      <BiMessageAdd/>
    </span>
  )
}

export default NewChatButton
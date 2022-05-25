import React from 'react';
import AvatarMini from '../Avatars/AvatarMini'

const TextMessage = ({message, fromMe}) => {
  const {avatar_file: avatarFile, text, time, login} = message

  return (
    <>
      <div className={`d-flex ${fromMe ? 'flex-row-reverse' : 'flex-row'}`}>
        <AvatarMini fileName={avatarFile}/>
        <div
          className={`mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
        >
          {text}
        </div>
      </div>
      <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
        {fromMe ? 'Вы' : login}, {time}
      </div>
    </>
  )
}

export default TextMessage
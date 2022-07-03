import React from 'react'

const InfoMessage = ({message}) => {
  const {text, time} = message

  return (
    <div className="p-1 align-self-center text-muted" style={{fontSize: 14}}>
      {time}, {text}
    </div>
  )
}

export default InfoMessage
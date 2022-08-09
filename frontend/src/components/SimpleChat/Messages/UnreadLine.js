import React from 'react'

const UnreadLine = () => {
  return (
    <div
      className="py-1 px-2 text-primary border border-primary"
    >
      <span className="me-2">&#8595;</span>
      Непрочитанные сообщения
      <span className="ms-2">&#8595;</span>
    </div>
  )
}

export default UnreadLine
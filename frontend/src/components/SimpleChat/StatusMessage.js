import React from 'react'

const StatusMessage = ({fromMe, message}) => {
  if (fromMe)
    return null

  const statusBgColorMap = {
    "ONLINE": "bg-success",
    "OFFLINE": "bg-danger"
  }

  const {online_status: onlineStatus, time, text} = message

  return (
    <>
      <div className="d-flex flex-row">
        <div className={`mx-2 rounded px-2 py-1 text-white border ${statusBgColorMap[onlineStatus]}`}>
          {text}
        </div>
      </div>
      <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
        {time}
      </div>
    </>
  )
}

export default StatusMessage
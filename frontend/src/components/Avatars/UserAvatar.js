import React from 'react'
import {Image} from 'react-bootstrap'

import {API_URL} from '../../axios/axios'

const UserAvatar = ({login, size = "sm"}) => {
  const sizeMapping = {
    sm: 40,
    md: 100,
    lg: 200
  }
  return (
    <Image
      roundedCircle={true}
      src={`${API_URL}/user/avatar_file/${login}`}
      alt="аватар"
      style={{height: sizeMapping[size], width: 'auto'}}
    />
  )
}

export default UserAvatar

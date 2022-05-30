import React from 'react'
import {Image} from 'react-bootstrap'

import noAvatar from '../../img/no_avatar.png'
import {API_URL} from '../../axios/axios'

const Avatar = ({fileName, size = "sm"}) => {
  const sizeMapping = {
    sm: 40,
    md: 100,
    lg: 200
  }
  const avatarSrc = fileName ? `${API_URL}/static/${fileName}` : noAvatar
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: sizeMapping[size], width: 'auto'}}
    />
  )
}

export default Avatar
import React from 'react'
import {Image} from 'react-bootstrap'

import {API_URL} from '../../axios/axios'
import noAvatar from '../../img/no_avatar.png'


const FileAvatar = ({fileName, size = "sm"}) => {
  const avatarSrc = fileName ? `${API_URL}/files/${fileName}` : noAvatar
  const sizeMapping = {
    sm: 40,
    md: 100,
    lg: 200
  }
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: sizeMapping[size], width: 'auto'}}
    />
  )
}

export default FileAvatar
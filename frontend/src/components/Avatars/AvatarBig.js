import React from 'react'
import {Image} from 'react-bootstrap'

import noAvatar from '../../img/no_avatar.png'
import {observer} from 'mobx-react-lite'
import {API_URL} from '../../axios/axios'

const AvatarBig = ({fileName}) => {
  const avatarSrc = fileName ? `${API_URL}/static/${fileName}` : noAvatar
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: 200, width: 'auto'}}
    />
  )
}

export default observer(AvatarBig)
import React from 'react'
import {Image} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import noAvatar from '../../img/no_avatar.png'
import {API_URL} from '../../axios/axios'


const AvatarMini = ({fileName}) => {
  const avatarSrc = fileName ? `${API_URL}/static/${fileName}` : noAvatar
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: 40, width: 'auto'}}
    />
  )
}

export default observer(AvatarMini)
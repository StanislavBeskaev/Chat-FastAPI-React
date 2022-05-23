import React from 'react'
import {Button, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'
import {Link} from 'react-router-dom'

import authStore from '../../stores/authStore'
import AvatarMini from '../../components/Avatars/AvatarMini'
import SimpleChat from '../../components/SimpleChat/SimpleChat'


const Main = () => {
  return (
    <div className="m-4">
      <div className="d-flex justify-content-around">
        <div>
          <h2 className="mb-4">Добро пожаловать: {authStore.user.login}</h2>
          <Row className="mb-3">
            <AvatarMini />
          </Row>
          <Button onClick={() => authStore.logout()} variant="danger" className="ms-3">Выход</Button>
          <Row className="mt-3">
            <Link to="/user-data/">Данные пользователя</Link>
          </Row>
        </div>
        <SimpleChat />
      </div>



    </div>
  )
}

export default observer(Main)
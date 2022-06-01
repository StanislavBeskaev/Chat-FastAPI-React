import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Tab, Nav, Button, Row} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import AvatarMini from '../Avatars/AvatarMini'
import authStore from '../../stores/authStore'
import Chats from './Chats'


const CONVERSATIONS_KEY = 'conversation'

function Sidebar({ login }) {
  const [activeKey, setActiveKey] = useState(CONVERSATIONS_KEY)

  return (
    <div style={{width: '290px'}} className="d-flex flex-column">
      <Tab.Container activeKey={activeKey} onSelect={setActiveKey}>
        <Nav variant="tabs" className="justify-content-center">
          <Nav.Item>
            <Nav.Link eventKey={CONVERSATIONS_KEY} className="btn">Чаты</Nav.Link>
          </Nav.Item>
        </Nav>
        <Tab.Content className="border-end overflow-auto flex-grow-1">
          <Tab.Pane eventKey={CONVERSATIONS_KEY}>
            <Chats/>
          </Tab.Pane>
        </Tab.Content>
        <div className="p-2 border-top border-end small">
          <div className="d-flex flex-column">
            <div>
              <AvatarMini fileName={authStore.avatarFile}/>
              <span className="ms-2">
                Ваш логин: <span className="text-muted">{login}</span>
              </span>
            </div>
            <Button
                onClick={() => authStore.logout()}
                size="sm"
                variant="danger"
                className="ms-3 align-self-end"
            >
              Выход
            </Button>
          </div>
          <Row className="mt-3">
            <Link to="/user-data/">Данные пользователя</Link>
          </Row>
        </div>
      </Tab.Container>
    </div>
  )
}

export default observer(Sidebar)
import React, {useState} from 'react'
import {Tab, Nav, Button, Row} from 'react-bootstrap'
import AvatarMini from './Avatars/AvatarMini'
import authStore from '../stores/authStore'
import {Link} from 'react-router-dom'


const CONVERSATIONS_KEY = 'conversation'

export default function Sidebar({ login }) {
  const [activeKey, setActiveKey] = useState(CONVERSATIONS_KEY)

  return (
    <div style={{width: '290px'}} className="d-flex flex-column">
      <Tab.Container activeKey={activeKey} onSelect={setActiveKey}>
        <Nav variant="tabs" className="justify-content-center">
          <Nav.Item>
            <Nav.Link eventKey={CONVERSATIONS_KEY} className="btn">Conversations</Nav.Link>
          </Nav.Item>
        </Nav>
        <Tab.Content className="border-end overflow-auto flex-grow-1">
          <Tab.Pane eventKey={CONVERSATIONS_KEY}>
            <h3>Тут будут чаты</h3>
          </Tab.Pane>
        </Tab.Content>
        <div className="p-2 border-top border-end small">
          <div>
            <AvatarMini fileName={authStore.avatarFile} />
            <span className="ms-2">
            Ваш логин: <span className="text-muted">{login}</span>
          </span>
            <Button onClick={() => authStore.logout()} size="sm" variant="danger" className="ms-3">Выход</Button>
          </div>

          <Row className="mt-3">
            <Link to="/user-data/">Данные пользователя</Link>
          </Row>
        </div>
      </Tab.Container>
    </div>
  )
}
import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Tab, Nav, Button, Row, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import AvatarMini from '../Avatars/AvatarMini'
import authStore from '../../stores/authStore'
import Chats from './Chats'
import Contacts from './Contacts'
import contactModalStore from '../../stores/modals/contactModalStore'
import ContactModal from '../Modals/ContactModal'


const CHATS_KEY = 'conversation'
const CONTACTS_KEY = 'contacts'

function Sidebar({ login }) {
  const [activeKey, setActiveKey] = useState(CHATS_KEY)

  return (
    <div style={{width: '290px'}} className="d-flex flex-column">
      <Tab.Container activeKey={activeKey} onSelect={setActiveKey}>
        <Nav variant="tabs" className="justify-content-center">
          <Nav.Item>
            <Nav.Link eventKey={CHATS_KEY} className="btn">Чаты</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey={CONTACTS_KEY} className="btn">Контакты</Nav.Link>
          </Nav.Item>
        </Nav>
        <Tab.Content className="border-end overflow-auto flex-grow-1">
          <Tab.Pane eventKey={CHATS_KEY}>
            <Chats/>
          </Tab.Pane>
          <Tab.Pane eventKey={CONTACTS_KEY}>
            <Contacts />
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
      <Modal show={contactModalStore.show} onHide={() => contactModalStore.close()}>
        <ContactModal/>
      </Modal>
    </div>
  )
}

export default observer(Sidebar)

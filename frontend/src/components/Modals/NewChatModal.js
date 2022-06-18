import React from 'react'
import {observer} from 'mobx-react-lite'
import {Button, Modal} from 'react-bootstrap'

import messagesStore from '../../stores/messagesStore'


const NewChatModal = () => {

  return (
    <>
      <Modal.Body>
        <h6>Создание нового чата</h6>
        <div className="d-flex m-4">
          <Button
            size="sm"
            variant="primary"
            onClick={async () => {
              //  TODO модалка для создания чата
              console.log("Тут будет создание нового чата")
              await messagesStore.sendNewChatRequest()
            }}
          >
            Создать
          </Button>
        </div>
      </Modal.Body>
    </>
  )
}

export default observer(NewChatModal)
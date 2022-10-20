import React, {useState} from 'react'
import {Badge, Button} from "react-bootstrap"
import confirmDeleteModalStore from "../../../stores/modals/confirmDeleteModalStore";
import messagesStore from "../../../stores/messagesStore";


const Chat = ({chatId, chatName, selected,  notViewedMessagesCount}) => {
    const  [showDeleteBtn, setShowDeleteBtn] = useState(false)

    const handleDelete = async (e) => {
      e.stopPropagation()
      //  TODO выполнить запрос на выход из чата при да
      const warningMessage = await messagesStore.tryLeaveChat(chatId)
      confirmDeleteModalStore.open(
        warningMessage,
      () => {},
      () => {}
      )
    }

    return (
        <div
          className="d-flex justify-content-between"
          onMouseOver={() => setShowDeleteBtn(true)}
          onMouseOut={() => setShowDeleteBtn(false)}
        >
            {chatName}
            <div className="d-flex gap-1">
              {
                notViewedMessagesCount > 0
                  ? <Badge
                      pill
                      bg={selected ? 'light' : 'primary'}
                      className={`align-self-center ${selected ? 'text-primary' : ''}`}
                    >
                      {notViewedMessagesCount}
                    </Badge>
                  : null
              }
              {
                showDeleteBtn && chatId !== "MAIN"
                  ? <Button style={{fontSize: 8}} variant="danger" size="sm" onClick={handleDelete}>X</Button>
                  : null
              }
            </div>
        </div>
    )
}

export default Chat
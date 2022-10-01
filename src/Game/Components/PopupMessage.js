import React from 'react';

const PopupMessage = ({message}) => {
    return (
        <div className='w-64 rounded-lg z-10 px-4 py-6 bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' >
            <p className='font-bold text-xl text-center text-[#3EA66C]' >{message}</p>
        </div>
    );
};

export default PopupMessage;
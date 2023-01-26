import React from 'react';

const CancelSeatRequest = ({cancelSeat}) => {
    return (
        <div 
            onClick={e => cancelSeat()}
            className='text-sm w-fit ml-auto mr-2 mt-2 p-2 border-2 rounded-lg border-red-600 text-red-500' >
            Cancel Seat Request
        </div>
    );
};

export default CancelSeatRequest;
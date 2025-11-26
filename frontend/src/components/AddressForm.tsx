import React from 'react'
import { useFormik } from 'formik'
import * as Yup from 'yup'
import { Address, CreateAddressRequest } from '../types/user'

interface AddressFormProps {
  address?: Address
  onSubmit: (data: CreateAddressRequest) => Promise<void>
  onCancel?: () => void
  isLoading?: boolean
}

const addressValidationSchema = Yup.object({
  name: Yup.string().required('Name is required'),
  phone: Yup.string()
    .matches(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format')
    .required('Phone number is required'),
  address_line1: Yup.string().required('Address line 1 is required'),
  address_line2: Yup.string(),
  city: Yup.string().required('City is required'),
  state: Yup.string().required('State is required'),
  postal_code: Yup.string()
    .matches(/^\d{6}$/, 'Postal code must be 6 digits')
    .required('Postal code is required'),
  country: Yup.string().required('Country is required'),
  is_default: Yup.boolean(),
})

const AddressForm: React.FC<AddressFormProps> = ({ address, onSubmit, onCancel, isLoading }) => {
  const formik = useFormik({
    initialValues: {
      name: address?.name || '',
      phone: address?.phone || '',
      address_line1: address?.address_line1 || '',
      address_line2: address?.address_line2 || '',
      city: address?.city || '',
      state: address?.state || '',
      postal_code: address?.postal_code || '',
      country: address?.country || 'India',
      is_default: address?.is_default || false,
    },
    validationSchema: addressValidationSchema,
    onSubmit: async (values) => {
      await onSubmit(values)
    },
  })

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Full Name *
          </label>
          <input
            id="name"
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...formik.getFieldProps('name')}
          />
          {formik.touched.name && formik.errors.name && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.name}</p>
          )}
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
            Phone Number *
          </label>
          <input
            id="phone"
            type="tel"
            placeholder="+911234567890"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...formik.getFieldProps('phone')}
          />
          {formik.touched.phone && formik.errors.phone && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.phone}</p>
          )}
        </div>
      </div>

      {/* Address Line 1 */}
      <div>
        <label htmlFor="address_line1" className="block text-sm font-medium text-gray-700">
          Address Line 1 *
        </label>
        <input
          id="address_line1"
          type="text"
          placeholder="House/Flat No., Building Name"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
          {...formik.getFieldProps('address_line1')}
        />
        {formik.touched.address_line1 && formik.errors.address_line1 && (
          <p className="mt-1 text-sm text-red-600">{formik.errors.address_line1}</p>
        )}
      </div>

      {/* Address Line 2 */}
      <div>
        <label htmlFor="address_line2" className="block text-sm font-medium text-gray-700">
          Address Line 2
        </label>
        <input
          id="address_line2"
          type="text"
          placeholder="Street, Area, Landmark"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
          {...formik.getFieldProps('address_line2')}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* City */}
        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-700">
            City *
          </label>
          <input
            id="city"
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...formik.getFieldProps('city')}
          />
          {formik.touched.city && formik.errors.city && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.city}</p>
          )}
        </div>

        {/* State */}
        <div>
          <label htmlFor="state" className="block text-sm font-medium text-gray-700">
            State *
          </label>
          <input
            id="state"
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...formik.getFieldProps('state')}
          />
          {formik.touched.state && formik.errors.state && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.state}</p>
          )}
        </div>

        {/* Postal Code */}
        <div>
          <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700">
            Postal Code *
          </label>
          <input
            id="postal_code"
            type="text"
            placeholder="123456"
            maxLength={6}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
            {...formik.getFieldProps('postal_code')}
          />
          {formik.touched.postal_code && formik.errors.postal_code && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.postal_code}</p>
          )}
        </div>
      </div>

      {/* Country */}
      <div>
        <label htmlFor="country" className="block text-sm font-medium text-gray-700">
          Country *
        </label>
        <input
          id="country"
          type="text"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm px-3 py-2 border"
          {...formik.getFieldProps('country')}
        />
        {formik.touched.country && formik.errors.country && (
          <p className="mt-1 text-sm text-red-600">{formik.errors.country}</p>
        )}
      </div>

      {/* Default Address Checkbox */}
      <div className="flex items-center">
        <input
          id="is_default"
          name="is_default"
          type="checkbox"
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          checked={formik.values.is_default}
          onChange={formik.handleChange}
        />
        <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
          Set as default address
        </label>
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : address ? 'Update Address' : 'Add Address'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export default AddressForm

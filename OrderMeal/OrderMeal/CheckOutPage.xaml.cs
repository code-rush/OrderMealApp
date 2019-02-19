using System;
using System.Collections.Generic;

using Xamarin.Forms;

namespace OrderMeal
{
    public partial class CheckOutPage : ContentPage
    {

        public CheckOutPage(string optionOneMeals, string optionTwoMeals)
        {
            InitializeComponent();
            Option1Count.Text = optionOneMeals;
            Option2Count.Text = optionTwoMeals;
            var totalMealOptionOnePrice = Convert.ToInt32(optionOneMeals) * 20;
            var totalMealOptionTwoPrice = Convert.ToInt32(optionTwoMeals) * 24;
            var tax = (totalMealOptionOnePrice + totalMealOptionTwoPrice) * 0.09;
            var totalPrice = totalMealOptionOnePrice + totalMealOptionTwoPrice + tax;
            Tax.Text = "$" + tax.ToString();
            TotalPrice.Text = "$" + totalPrice.ToString();

            if (Application.Current.Properties.ContainsKey("user_id")) { fullName.Text = Application.Current.Properties["user_id"].ToString(); }
            if (Application.Current.Properties.ContainsKey("email")) { emailAddress.Text = Application.Current.Properties["email"].ToString(); }
            if (Application.Current.Properties.ContainsKey("phone")) { phoneNumber.Text = Application.Current.Properties["phone"].ToString(); }
            if (Application.Current.Properties.ContainsKey("street")) { streetAddress.Text = Application.Current.Properties["street"].ToString(); }
            if (Application.Current.Properties.ContainsKey("city")) { City.Text = Application.Current.Properties["city"].ToString(); }
            if (Application.Current.Properties.ContainsKey("state")) { State.Text = Application.Current.Properties["state"].ToString(); }
            if (Application.Current.Properties.ContainsKey("zip")) { zipCode.Text = Application.Current.Properties["zip"].ToString(); }
        }

        void Handle_Clicked(object sender, System.EventArgs e)
        {
            if (fullName.Text != "") { Application.Current.Properties["user_id"] = fullName.Text; }

            System.Diagnostics.Debug.Print(Application.Current.Properties["user_id"].ToString());

            if (emailAddress.Text != "") { Application.Current.Properties["email"] = emailAddress.Text; }
            if (phoneNumber.Text != "") { Application.Current.Properties["phone"] = phoneNumber.Text; }
            if (streetAddress.Text != "") { Application.Current.Properties["street"] = streetAddress.Text; }
            if (City.Text != "") { Application.Current.Properties["city"] = City.Text; }
            if (State.Text != "") { Application.Current.Properties["state"] = State.Text; }
            if (zipCode.Text != "") { Application.Current.Properties["zip"] = zipCode.Text; }
            Application.Current.SavePropertiesAsync();
            //var client = HttpClient();
        }
    }
}
